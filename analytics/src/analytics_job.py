from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col
from .config import ORDERS_JSONL, PRODUCTS_CSV, STORES_CSV, OUTPUT_DIR, Config, ColumnNames
from .utils import load_environment, ensure_output_dir
from .logger_config import logger  # Import logger

def load_data(spark, file_path, format_type="csv", **kwargs):
    try:
        logger.info(f"Loading {format_type} data from: {file_path}")
        if format_type == "json":
            df = spark.read.json(file_path)
        else:
            df = spark.read.csv(file_path, **kwargs)
        logger.debug(f"Successfully loaded {df.count()} rows")
        return df
    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {str(e)}")
        raise

def process_orders(orders_df):
    return orders_df.select(
        col(ColumnNames.Order.ID).alias(ColumnNames.Item.ORDER_ID),
        explode(ColumnNames.Order.ITEMS).alias("item"),
        ColumnNames.Order.CUSTOMER_NAME,
        ColumnNames.Order.CUSTOMER_CONTACT,
        ColumnNames.Order.DELIVERY_ADDRESS,
        ColumnNames.Order.STATUS,
        ColumnNames.Order.CREATED_AT
    )

def main():
    logger.info("Starting Analytics Job")
    # Ensure environment is loaded
    load_environment()
    
    spark = None
    try:
        spark = SparkSession.builder.appName("AnalyticsJob").getOrCreate()
        ensure_output_dir(OUTPUT_DIR)

        # Load data with error handling
        orders = load_data(spark, ORDERS_JSONL, format_type="json")
        products = load_data(spark, PRODUCTS_CSV, header=True, inferSchema=True)
        stores = load_data(spark, STORES_CSV, header=True, inferSchema=True)

        logger.info("Processing order items")
        order_items = process_orders(orders)
        order_items = order_items.select(
            "order_id",
            col("item.product_id").alias("product_id"),
            col("item.quantity").alias("quantity"),
            col("item.price").alias("price"),
            "customer_name",
            "customer_contact",
            "delivery_address",
            "status",
            "created_at"
        )

        logger.info("Calculating total sales per product")
        sales_per_product = order_items.groupBy("product_id").sum("price").withColumnRenamed("sum(price)", "total_sales")
        sales_per_product = sales_per_product.join(products, order_items.product_id == products.id, "left").select(
            products.name.alias("product_name"), sales_per_product.total_sales
        )
        sales_per_product.show()
        sales_per_product.coalesce(1).write.csv(f"{OUTPUT_DIR}/sales_per_product", header=True, mode="overwrite")

        logger.info("Calculating order volume per store")
        order_items_with_store = order_items.join(products, order_items.product_id == products.id, "left")
        order_volume_per_store = order_items_with_store.groupBy("store_id").count().withColumnRenamed("count", "order_count")
        order_volume_per_store = order_volume_per_store.join(stores, order_volume_per_store.store_id == stores.id, "left").select(
            stores.name.alias("store_name"), order_volume_per_store.order_count
        )
        order_volume_per_store.show()
        order_volume_per_store.coalesce(1).write.csv(f"{OUTPUT_DIR}/order_volume_per_store", header=True, mode="overwrite")

        logger.info("Analytics jobs completed. Output written to: %s", OUTPUT_DIR)
    except Exception as e:
        logger.error(f"Analytics job failed: {str(e)}")
        raise
    finally:
        if spark:
            logger.info("Stopping Spark session")
            spark.stop()

if __name__ == "__main__":
    main()
