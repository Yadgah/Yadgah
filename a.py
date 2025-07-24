def fibonacci(n):
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        print(_)
        sequence.append(a)
        a, b = b, a + b
    return sequence

# نمونه استفاده
num_terms = int(input("تعداد عبارات فیبوناچی مورد نظر را وارد کنید: "))
print(f"سری فیبوناچی تا {num_terms} عبارت: {fibonacci(num_terms)}")