from student import StudentGroup
from student import Student
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool


def main():
    group = StudentGroup()
    # group.import_database()
    try:
        group.pull_database()
        # group.all_get_courses()
        group.all_info()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
