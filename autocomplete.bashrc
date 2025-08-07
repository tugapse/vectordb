_vectordb_completion() {
    local cur prev words cword
    _init_completion || return

    COMPREPLY=()

    local all_commands="collection document"

    # Handle main command arguments
    if [[ ${cword} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${all_commands}" -- "${cur}") )
        return
    fi

    local main_command="${words[1]}"
    local main_flags="--db-path --db-name --json -h --help"

    # Handle completion for main flags
    if [[ "${cur}" == --* ]] || [[ "${prev}" == --* ]]; then
        COMPREPLY=( $(compgen -W "${main_flags}" -- "${cur}") )
    fi

    # Handle completion for subcommands and their arguments
    case "${main_command}" in
        collection)
            local collection_commands="create delete list"
            local collection_flags="-h --help"
            
            if [[ ${cword} -eq 2 ]]; then
                COMPREPLY=( $(compgen -W "${collection_commands}" -- "${cur}") )
                return
            fi

            # Handle subcommand-specific flags
            if [[ "${cur}" == --* ]]; then
                COMPREPLY=( $(compgen -W "${collection_flags}" -- "${cur}") )
                return
            fi
            ;;

        document)
            local document_commands="add query delete list"
            local document_flags="-h --help"

            if [[ ${cword} -eq 2 ]]; then
                COMPREPLY=( $(compgen -W "${document_commands}" -- "${cur}") )
                return
            fi

            local document_subcommand="${words[2]}"
            
            # Handle document subcommand arguments and flags
            case "${document_subcommand}" in
                add)
                    local add_flags="--text --metadata --id -h --help"
                    COMPREPLY=( $(compgen -W "${add_flags}" -- "${cur}") )
                    ;;
                query)
                    local query_flags="--query-text --n-results --where --where-document -h --help"
                    COMPREPLY=( $(compgen -W "${query_flags}" -- "${cur}") )
                    ;;
                delete)
                    local delete_flags="--id --where --where-document -h --help"
                    COMPREPLY=( $(compgen -W "${delete_flags}" -- "${cur}") )
                    ;;
                list)
                    # The 'list' command has no flags, only the collection name argument
                    COMPREPLY=()
                    ;;
            esac
            ;;
    esac

    return
}

# The `_init_completion` function is a bash-completion utility that helps set up
# completion variables like `COMP_WORDS`, `COMP_CWORD`, and `COMPREPLY`.
# While it's part of the standard bash-completion package, it might not be
# available on every system. If you run into issues, you may need to
# install `bash-completion` via your package manager (e.g., `sudo apt-get install bash-completion`).
# Then, you would typically source its main script in your .bashrc, for example:
# source /etc/bash_completion
#
# If you don't have the `bash-completion` package, you can still use the script
# by defining the necessary variables yourself, but the provided `_init_completion`
# call simplifies this.

complete -F _vectordb_completion vectordb