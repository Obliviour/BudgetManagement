import csv
import argparse


def main():
    """takes in a csv file and reads in project budget information"""
    parser = argparse.ArgumentParser(description='Provide budgets to generate transactions list')
    parser.add_argument('csv_name', help='String name of the csv file with budget info in three '
                                         'columns, see template.csv')
    parser.add_argument('transaction_csv', help='transactions written to this csv, make sure different from the first '
                                                'csv sheet')
    args = parser.parse_args()
    account_dict = read_csv(args.csv_name)
    check_valid_account(account_dict)
    transaction_dict = generate_transactions(account_dict)
    write_csv(args.transaction_csv, transaction_dict)


def read_csv(csv_name):
    """create dictionary with net gain required to get from current balance to new balance"""
    with open(csv_name, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        account_dict = {}
        line_count = 0
        for row in csv_reader:
            # print(f'row: {row}')
            if line_count == 0:
                keys = [k for k, _ in row.items()]

            after = float("{0:.2f}".format(float(row[keys[2]])))
            before = float("{0:.2f}".format(float(row[keys[1]])))
            account_dict[row[keys[0]]] = after - before
            line_count += 1
    return account_dict


def check_valid_account(account_dict):
    """check that the starting balance and ending balance sum up to the same"""
    if sum(account_dict.values()) >= 1e-5:
        print(sum(account_dict.values()))
        print("Improper Account Information, Check that Overall Start and End Budget are the same\n")
        raise(Exception("Improper Account Information, Check that Overall Start and End Budget are the same"))
    return


def generate_transactions(account_dict):
    """generates a dictionary listing the transactions that will be taken to move budget from current to new"""
    transaction_dict = {}
    transaction_number = 0
    while not_balanced(account_dict):
        transaction_number += 1

        max_key, max_val = max(account_dict.items(), key=(lambda key: account_dict[key[0]]))
        min_key, min_val = min(account_dict.items(), key=(lambda key: account_dict[key[0]]))
        for k, v in account_dict.items():
            for k2, v2 in account_dict.items():
                if v == -v2 and v != 0:
                    # simplified transaction
                    max_key, min_key = k2, k
                    max_val, min_val = v2, v

        transaction_amount = min(max_val, abs(min_val))
        transaction_amount = float("{0:.2f}".format(transaction_amount))
        print(f'min_key: {min_key}, max_key: {max_key}, transaction_amount: {transaction_amount}\n')
        print(account_dict)
        transaction_dict[transaction_number] = [min_key, max_key, transaction_amount]
        account_dict[max_key] -= transaction_amount
        account_dict[min_key] += transaction_amount
        print(f'{transaction_dict}\n')
    return transaction_dict


def not_balanced(account_dict):
    """checks if accounts have been fulled balanced by checking if account differences are all zero
    if all accounts are zero, return False else return True"""
    for _, v in account_dict.items():
        if v >= 1e-5:
            return True
    return False


def write_csv(transaction_csv, transaction_dict):
    """write results to new csv file to view transactions"""
    with open(transaction_csv, mode="w") as csv_file:
        fieldnames = ['Transaction Number', 'From (Project)', 'To (Project)', 'Transaction Amount']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for k, v in transaction_dict.items():
            writer.writerow({'Transaction Number': k, 'From (Project)': v[0], 'To (Project)': v[1],
                             'Transaction Amount': v[2]})


if __name__ == "__main__":
    main()
