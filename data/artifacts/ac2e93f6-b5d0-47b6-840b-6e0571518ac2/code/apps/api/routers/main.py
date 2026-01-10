from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# --- SQLAlchemy related imports (Placeholders for actual setup) ---
# In a real application, these would be used to configure your database connection
# from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy.sql import func # For default timestamps

# DATABASE_URL = "postgresql://user:password@host:port/dbname"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# --- Mock Database and Model for demonstration without a live DB ---
# This section simulates SQLAlchemy ORM behavior for local execution.
# In a real project, you would uncomment the SQLAlchemy imports above
# and define your models and session management properly.

class MockColumn:
    """A mock Column object to allow attribute access like ProductModel.id"""
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        # This allows expressions like ProductModel.id == product_id
        class Comparison:
            def __init__(self, left, right):
                self.left = left
                self.right = right
            def __bool__(self): return False # Not a real boolean
        return Comparison(self, other)

class ProductModel:
    """
    A mock SQLAlchemy-like model for a Product.
    In a real application, this would inherit from Base (declarative_base()).
    """
    id: Optional[int] = MockColumn('id')
    name: str = MockColumn('name')
    description: Optional[str] = MockColumn('description')
    price: float = MockColumn('price')
    stock_quantity: int = MockColumn('stock_quantity')
    is_active: bool = MockColumn('is_active')
    category_id: Optional[int] = MockColumn('category_id')
    created_at: datetime = MockColumn('created_at')
    updated_at: datetime = MockColumn('updated_at')

    def __init__(self, name: str, description: Optional[str], price: float, stock_quantity: int, is_active: bool, category_id: Optional[int] = None):
        self.id = None # Will be set by MockDB
        self.name = name
        self.description = description
        self.price = price
        self.stock_quantity = stock_quantity
        self.is_active = is_active
        self.category_id = category_id
        self.created_at = None # Will be set by MockDB
        self.updated_at = None # Will be set by MockDB

    def __repr__(self):
        return f"<ProductModel(id={self.id}, name='{self.name}')>"

class MockDB:
    """
    A mock database session manager that simulates SQLAlchemy's Session.
    Stores ProductModel instances in a list.
    """
    def __init__(self):
        self.products: List[ProductModel] = []
        self._next_id = 1

    def add(self, item: ProductModel):
        item.id = self._next_id
        item.created_at = datetime.utcnow()
        item.updated_at = datetime.utcnow()
        self._next_id += 1
        self.products.append(item)
        return item

    def query(self, model_class):
        """Simulates session.query(Model)"""
        class MockQuery:
            def __init__(self, items_list):
                self._items = items_list

            def all(self):
                return self._items

            def filter(self, comparison):
                # This is a very simplistic filter for demonstration
                # It expects a comparison object from MockColumn.__eq__
                if hasattr(comparison, 'left') and hasattr(comparison, 'right'):
                    field_name = comparison.left.name
                    value = comparison.right
                    filtered_items = [item for item in self._items if getattr(item, field_name) == value]
                    return MockQuery(filtered_items)
                return self # If filter is called without a valid comparison

            def first(self):
                return self._items[0] if self._items else None

            def offset(self, skip: int):
                return MockQuery(self._items[skip:])

            def limit(self, limit: int):
                return MockQuery(self._items[:limit])

        return MockQuery(self.products)

    def delete(self, item: ProductModel):
        if item in self.products:
            self.products.remove(item)

    def refresh(self, item: ProductModel):
        # In a real DB, this would re-load attributes from the DB.
        # For mock, we just ensure updated_at is set.
        item.updated_at = datetime.utcnow()
        pass

    def commit(self):
        # No-op for mock, as changes are immediate in the list
        pass

mock_db_instance = MockDB()

# --- Pydantic Schemas ---

# Base Schema for common fields
class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Name of the product")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description of the product")
    price: float = Field(..., gt=0, description="Price of the product, must be greater than 0")
    stock_quantity: int = Field(..., ge=0, description="Current stock quantity, must be non-negative")
    is_active: bool = Field(True, description="Whether the product is currently active and available")
    category_id: Optional[int] = Field(None, description="ID of the category this product belongs to")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop Pro X",
                "description": "High-performance laptop for professionals.",
                "price": 1299.99,
                "stock_quantity": 50,
                "is_active": True,
                "category_id": 101
            }
        }

# Schema for creating a new product
class ProductCreate(ProductBase):
    pass

# Schema for updating an existing product (all fields optional)
class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Name of the product")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description of the product")
    price: Optional[float] = Field(None, gt=0, description="Price of the product, must be greater than 0")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Current stock quantity, must be non-negative")
    is_active: Optional[bool] = Field(None, description="Whether the product is currently active and available")
    category_id: Optional[int] = Field(None, description="ID of the category this product belongs to")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop Pro X (2024 Model)",
                "price": 1399.99,
                "stock_quantity": 45,
                "is_active": True
            }
        }

# Schema for returning a product response, including ID and timestamps
class ProductResponse(ProductBase):
    id: int = Field(..., description="Unique identifier of the product")
    created_at: datetime = Field(..., description="Timestamp when the product was created")
    updated_at: datetime = Field(..., description="Timestamp when the product was last updated")

    class Config:
        from_attributes = True # Enable ORM mode for Pydantic v2
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Laptop Pro X",
                "description": "High-performance laptop for professionals.",
                "price": 1299.99,
                "stock_quantity": 50,
                "is_active": True,
                "category_id": 101,
                "created_at": "2023-10-27T10:00:00.000Z",
                "updated_at": "2023-10-27T10:00:00.000Z"
            }
        }

# --- Dependencies ---

# Dependency to get a database session
def get_db():
    # db = SessionLocal() # Uncomment for real SQLAlchemy session
    db = mock_db_instance # Using mock DB for demonstration
    try:
        yield db
    finally:
        # db.close() # Uncomment for real SQLAlchemy session
        pass

# Placeholder for JWT authentication dependency
class CurrentUser:
    """Mock User object for authentication."""
    def __init__(self, id: int, email: str, is_admin: bool = False):
        self.id = id
        self.email = email
        self.is_admin = is_admin

def get_current_user():
    """
    Dependency to get the current authenticated user.
    In a real application, this would decode a JWT token from the request header.
    """
    # Simulate token validation and user retrieval
    # For demonstration, we return a mock admin user.
    # If authentication fails, raise HTTPException:
    # raise HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    mock_user = CurrentUser(id=1, email="admin@example.com", is_admin=True)
    return mock_user

# --- FastAPI Router Definition ---
router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Product not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_403_FORBIDDEN: {"description": "Not authorized"}
    }
)

# --- CRUD Operations ---

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: MockDB = Depends(get_db)
):
    """
    Create a new product in the E-commerce system.
    Requires authentication and admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators are allowed to create products"
        )

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    # db.commit() # TODO: Uncomment when DB is configured
    db.refresh(db_product)
    return ProductResponse.model_validate(db_product)


@router.get("/", response_model=List[ProductResponse])
async def read_products(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of items to return"),
    db: MockDB = Depends(get_db)
):
    """
    Retrieve a list of all products.
    This endpoint is publicly accessible.
    """
    products = db.query(ProductModel).offset(skip).limit(limit).all()
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int = Path(..., gt=0, description="The ID of the product to retrieve"),
    db: MockDB = Depends(get_db)
):
    """
    Retrieve a single product by its unique ID.
    This endpoint is publicly accessible.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_update: ProductUpdate,
    product_id: int = Path(..., gt=0, description="The ID of the product to update"),
    current_user: CurrentUser = Depends(get_current_user),
    db: MockDB = Depends(get_db)
):
    """
    Update an existing product by its ID.
    Requires authentication and admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators are allowed to update products"
        )

    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    update_data = product_update.model_dump(exclude_unset=True) # Only update fields that are provided
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db_product.updated_at = datetime.utcnow() # Manually update timestamp for mock
    # db.commit() # TODO: Uncomment when DB is configured
    db.refresh(db_product)
    return ProductResponse.model_validate(db_product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int = Path(..., gt=0, description="The ID of the product to delete"),
    current_user: CurrentUser = Depends(get_current_user),
    db: MockDB = Depends(get_db)
):
    """
    Delete a product by its ID.
    Requires authentication and admin privileges.
    Returns 204 No Content on successful deletion.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators are allowed to delete products"
        )

    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(db_product)
    # db.commit() # TODO: Uncomment when DB is configured
    return # FastAPI automatically returns 204 No Content for this status code