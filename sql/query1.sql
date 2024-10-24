SELECT
  date,
  SUM(SAFE_MULTIPLY(prod_price,prod_qty)) AS ventes
FROM
  transaction
WHERE
  date BETWEEN "2019-01-01" AND "2019-12-31"
GROUP BY
  date
ORDER BY
  date ASC