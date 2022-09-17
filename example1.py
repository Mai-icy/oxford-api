from myfunc import main


def tt1():
    with open("input\\input.txt", "r", encoding="utf-8") as f:
        word_list = [line.strip() for line in f.readlines() if line.strip()]
    print(word_list)
    total = ""
    for wd in word_list:
        try:
            new = main(wd)
            total += new + "\n"
            print(new)
        except Exception as e:
            print(repr(e))
            print(f"{wd}错误")
            continue

    with open("input\\output.txt", "w", encoding="utf-8") as f:
        f.write(total)


if __name__ == "__main__":
    tt1()
