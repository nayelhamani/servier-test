SELECT
  t.client_id,
  SUM(CASE
      WHEN p.product_type = "MEUBLE" THEN SAFE_MULTIPLY(t.prod_price,t.prod_qty)
  END) AS ventes_meuble,
  SUM(CASE
      WHEN p.product_type = "DECO" THEN SAFE_MULTIPLY(t.prod_price,t.prod_qty)
  END) AS ventes_deco,
FROM
  transaction t
JOIN
  product_nomenclature AS p
ON
  t.prod_id=p.product_id
WHERE
  date BETWEEN "2019-01-01" AND "2019-12-31"
GROUP BY
  t.client_id