#!/usr/bin/env bash
set -e


check()
{
    # TODO: maybe run the tests
    printf "no tests implemented\n"
    exit -1
}


rebuild()
{
    rm -rf dist/*
    python3 -m build
    twine check dist/*
}

publish_test()
{
    twine upload -r testpypi dist/*
}

publish_release()
{
    twine upload dist/*
}


main()
{
    printf "todo list '$*'\n"
    while [[ $1 ]]
    do
        command="$1"
        shift

        case $command in
            check) check ;;
            build) rebuild ;;
            push) publish_test ;;
            release) publish_release ;;
            *) printf "I don't know what '$command' means." ;;
        esac
    done
}

main "$@"
