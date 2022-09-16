from myfunc import main


def tt1():
    with open("input\\input.txt", "r", encoding="utf-8") as f:
        word_list = [line.strip() for line in f.readlines() if line.strip()]
    print(word_list)
    for wd in word_list:
        with open("input\\output.txt", "w", encoding="utf-8") as f:
            try:
                print(main(wd))
            except:
                print(f"{wd}错误")
                continue
            f.write(main(wd) + "\n")


if __name__ == "__main__":
    tt1()