WITH contract AS (
  SELECT
    stock_id
  FROM
    `ps-data-analytics-platform.proto_pricingAI.contract`

)
SELECT 
  *
FROM 
  contract
LEFT JOIN 
  `ps-data-analytics-platform.proto_pricingAI.stock_id_inspect_info` stock_id_info
  ON
  contract.stock_id = stock_id_info.stock_id