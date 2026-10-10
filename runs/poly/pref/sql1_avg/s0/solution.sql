SELECT dept, ROUND(AVG(salary), 2) AS avg_salary FROM employees GROUP BY dept HAVING COUNT(*) >= 2 ORDER BY avg_salary DESC;
