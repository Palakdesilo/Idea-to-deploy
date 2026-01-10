from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Numeric, UniqueConstraint, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Many-to-many association table for ProductVariant and VariantOptionValue
product_variant_options_association = Table(
    'product_variant_options_association',
    Base.metadata,
    Column('product_variant_id', Integer, ForeignKey('product_variants.id'), primary_key=True),
    Column('variant_option_value_id', Integer, ForeignKey('variant_option_values.id'), primary_key=True)
)

# Many-to-many association table for Order and Coupon
order_coupon_association = Table(
    'order_coupon_association',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('coupon_id', Integer, ForeignKey('coupons.id'), primary_key=True),
    Column('discount_applied', Numeric(10, 2), nullable=False, default=0.00)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    wishlist_items = relationship("WishlistItem", back_populates="user")
    questions = relationship("ProductQuestion", back_populates="user")
    answers = relationship("ProductAnswer", back_populates="user")

class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True) # Nullable for guest checkout addresses
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    phone_number = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True) # For guest checkout or order specific email

    is_default_shipping = Column(Boolean, default=False, nullable=False)
    is_default_billing = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="addresses")
    # shipping_orders and billing_orders relationships are defined on the Order model.

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="brand")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    short_description = Column(String(500), nullable=True)
    long_description = Column(Text, nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False) # Base price before variants
    sku = Column(String(100), unique=True, index=True, nullable=True) # SKU for the base product
    stock_quantity = Column(Integer, default=0, nullable=False) # For products without variants, or aggregate
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id"), index=True, nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), index=True, nullable=True)

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    images = relationship("ProductImage", back_populates="product", order_by="ProductImage.display_order")
    variants = relationship("ProductVariant", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    specifications = relationship("ProductSpecification", back_populates="product")
    questions = relationship("ProductQuestion", back_populates="product")

class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_main = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="images")

class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    price_modifier = Column(Numeric(10, 2), default=0.00, nullable=False) # Added to base_price
    stock_quantity = Column(Integer, default=0, nullable=False)
    image_id = Column(Integer, ForeignKey("product_images.id"), nullable=True) # Specific image for this variant

    product = relationship("Product", back_populates="variants")
    image = relationship("ProductImage") # One-to-one or one-to-many if multiple images per variant
    options = relationship("VariantOptionValue", secondary=product_variant_options_association, back_populates="product_variants")

class VariantOptionType(Base):
    __tablename__ = "variant_option_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False) # e.g., "Color", "Size", "Storage"

    values = relationship("VariantOptionValue", back_populates="option_type")

class VariantOptionValue(Base):
    __tablename__ = "variant_option_values"
    id = Column(Integer, primary_key=True, index=True)
    option_type_id = Column(Integer, ForeignKey("variant_option_types.id"), index=True, nullable=False)
    value = Column(String(100), nullable=False) # e.g., "Red", "Small", "256GB"

    option_type = relationship("VariantOptionType", back_populates="values")
    product_variants = relationship("ProductVariant", secondary=product_variant_options_association, back_populates="options")

    __table_args__ = (UniqueConstraint('option_type_id', 'value', name='_option_type_value_uc'),)

class ShippingMethod(Base):
    __tablename__ = "shipping_methods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False) # e.g., "Standard Shipping", "Express Shipping"
    description = Column(Text, nullable=True)
    cost = Column(Numeric(10, 2), nullable=False)
    estimated_delivery_days = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    orders = relationship("Order", back_populates="shipping_method")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True) # Nullable for guest orders
    order_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    subtotal_amount = Column(Numeric(10, 2), nullable=False) # Sum of item prices
    shipping_cost = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False) # subtotal + shipping + tax - discount
    status = Column(String(50), default="pending", nullable=False) # e.g., 'pending', 'processing', 'shipped', 'delivered', 'cancelled'
    payment_status = Column(String(50), default="pending", nullable=False) # e.g., 'paid', 'pending', 'failed'
    payment_method = Column(String(50), nullable=False) # e.g., 'Credit Card', 'PayPal'
    tracking_number = Column(String(100), nullable=True)

    shipping_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    billing_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False) # Can be same as shipping
    shipping_method_id = Column(Integer, ForeignKey("shipping_methods.id"), index=True, nullable=False)

    user = relationship("User", back_populates="orders")
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    shipping_method = relationship("ShippingMethod", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    applied_coupons = relationship("Coupon", secondary=order_coupon_association, back_populates="orders")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Numeric(10, 2), nullable=False) # Price at the time of order

    order = relationship("Order", back_populates="order_items")
    product_variant = relationship("ProductVariant")

    __table_args__ = (UniqueConstraint('order_id', 'product_variant_id', name='_order_product_variant_uc'),)

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True) # Nullable for guest carts
    session_id = Column(String(255), index=True, nullable=True) # For guest users, or if user not logged in
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), index=True, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="cart_items")
    product_variant = relationship("ProductVariant")

    __table_args__ = (
        UniqueConstraint('user_id', 'product_variant_id', name='_user_product_variant_uc', deferrable=True, initially='DEFERRED'),
        UniqueConstraint('session_id', 'product_variant_id', name='_session_product_variant_uc', deferrable=True, initially='DEFERRED')
    )

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    rating = Column(Integer, nullable=False) # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='_user_product_review_uc'),) # One review per user per product

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")

    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='_user_product_wishlist_uc'),) # One wishlist item per user per product

class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_type = Column(String(50), nullable=False) # e.g., 'percentage', 'fixed_amount'
    value = Column(Numeric(10, 2), nullable=False) # e.g., 10 for 10%, 20 for $20
    min_order_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    max_discount_amount = Column(Numeric(10, 2), nullable=True) # Optional cap on discount
    start_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    usage_limit = Column(Integer, nullable=True) # Total uses across all users
    per_user_limit = Column(Integer, nullable=True) # Uses per user
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    orders = relationship("Order", secondary=order_coupon_association, back_populates="applied_coupons")

class NewsletterSubscription(Base):
    __tablename__ = "newsletter_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class ProductSpecification(Base):
    __tablename__ = "product_specifications"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    name = Column(String(100), nullable=False) # e.g., "Processor", "RAM"
    value = Column(String(255), nullable=False) # e.g., "A17 Bionic", "8GB"
    display_order = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="specifications")

    __table_args__ = (UniqueConstraint('product_id', 'name', name='_product_spec_name_uc'),)

class ProductQuestion(Base):
    __tablename__ = "product_questions"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True) # Nullable for anonymous questions
    question_text = Column(Text, nullable=False)
    asked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)

    product = relationship("Product", back_populates="questions")
    user = relationship("User", back_populates="questions")
    answers = relationship("ProductAnswer", back_populates="question")

class ProductAnswer(Base):
    __tablename__ = "product_answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("product_questions.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True) # Nullable for admin/guest answers
    answer_text = Column(Text, nullable=False)
    answered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)

    question = relationship("ProductQuestion", back_populates="answers")
    user = relationship("User", back_populates="answers")