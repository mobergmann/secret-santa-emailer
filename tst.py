import random
import time

def constraint(key_santas: "list[SecretSanta]", value_santas: "list[SecretSanta]") -> bool:
    """
    Checks that in two given lists no equal values have the same index: first_arr[i] != second_arr[i].
    In order to function, len(key_santas) must be equal to len(value_santas).
    :param key_santas: list of santas, who gift someone
    :param value_santas: list of santas, who are being gifted
    :return: true if the constraint is valid, false otherwise
    """

    for i in range(len(key_santas)):
        if key_santas[i] == value_santas[i]:
            return False
    return True

def wichtel():
    santas = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    tmp = santas.copy()
    result = []

    for santa in santas:
        try:
            tmp.remove(santa)

            if len(tmp) == 0:
                print("Alarm")
                print(tmp)
                print(result)
                print()
            
            r = random.randint(0, len(tmp)-1)

            result.append(tmp[r])
            tmp.remove(tmp[r])
            
            tmp.append(santa)
        except ValueError:
            r = random.randint(0, len(tmp)-1)

            result.append(tmp[r])
            tmp.remove(tmp[r])

    if not constraint(santas, result):
        print("panic")

for i in range(100):
    wichtel()
    print("step")
    time.sleep(1)





