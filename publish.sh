#!/usr/bin/env bash
set -e

# rm -rf dist/*
# python3 -m build
# twine upload -r testpypi dist/*

main()
{
    printf "commands queue '$*'\n"
    while [[ $1 ]]
    do
        command=$1
        printf " $command\n"
        shift
    done

}

main "$@"
