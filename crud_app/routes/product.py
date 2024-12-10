from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Product
from schemas import ProductCreate, ProductResponse  # Import the schemas
from services.logging_service import log_to_splunk

router = APIRouter()


@router.post(
    "/products/", response_model=ProductResponse
)  # Use ProductResponse for output
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(
        name=product.name, description=product.description, price=product.price
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    log_to_splunk(f"Created product: {product.name}")
    return db_product  # This can still return the full Product object


@router.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    log_to_splunk(f"Read product: {product_id}")
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductCreate,  # Use ProductCreate for input
    db: Session = Depends(get_db),
):
    existing_product = db.query(Product).filter(Product.id == product_id).first()
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    db.commit()
    log_to_splunk(f"Updated product: {product_id}")
    return existing_product


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    log_to_splunk(f"Deleted product: {product_id}")
    return {"message": "Product deleted"}
