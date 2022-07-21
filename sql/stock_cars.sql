WITH use_stockid_table AS (
  SELECT
    stock_id
  FROM 
    `ps-data-analytics-platform.proto_pricingAI.contract`
)
SELECT 
  date
  , stock_cars.stock_id
  , price
FROM 
  use_stockid_table use_stockid
INNER JOIN
  `ps-data-analytics-platform.proto_pricingAI.stock_cars` stock_cars
  ON
    use_stockid.stock_id = stock_cars.stock_id