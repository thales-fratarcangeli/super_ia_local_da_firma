SELECT dept, name, salary FROM (SELECT dept, name, salary, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC, id ASC) rn FROM employees) WHERE rn = 1 ORDER BY dept;
