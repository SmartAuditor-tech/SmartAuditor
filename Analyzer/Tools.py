ToolInfo = [

            {'name':'slither', 'docker':'No', 'command': 'slither','image':'smartbugs/slither','example': 'slither /path/to/Example.sol --json output.json','type':'contracts','usage':'''
  usage: slither target [flag]
No --timeout argument! Do not use it!
target can be:
        - file.sol // a Solidity file
        - project_directory // a project directory. See https://github.com/crytic/crytic-compile/#crytic-compile for the supported platforms
        - 0x.. // a contract on mainnet
        - NETWORK:0x.. // a contract on a different network. Supported networks: mainet,optim,goerli,sepolia,tobalaba,bsc,testnet.bsc,arbi,testnet.arbi,poly,mumbai,avax,testnet.avax,ftm,goerli.base,base,gno,polyzk

For usage information, see https://github.com/crytic/slither/wiki/Usage

options:
  -h, --help            show this help message and exit
  --version             displays the current version

Detectors:
  --detect DETECTORS_TO_RUN
                        Comma-separated list of detectors, defaults to all, available detectors: abiencoderv2-array, arbitrary-send-erc20, arbitrary-send-erc20-permit,
                        arbitrary-send-eth, array-by-reference, controlled-array-length, assembly, assert-state-change, backdoor, weak-prng, boolean-cst, boolean-equal,
                        shadowing-builtin, cache-array-length, codex, constant-function-asm, constant-function-state, pragma, controlled-delegatecall, costly-loop, constable-    
                        states, immutable-states, cyclomatic-complexity, dead-code, delegatecall-loop, deprecated-standards, divide-before-multiply, domain-separator-collision,  
                        encode-packed-collision, enum-conversion, external-function, function-init-state, erc20-interface, erc721-interface, incorrect-exp, incorrect-return,     
                        solc-version, incorrect-equality, incorrect-unary, incorrect-using-for, shadowing-local, locked-ether, low-level-calls, mapping-deletion, events-access,  
                        events-maths, missing-inheritance, missing-zero-check, incorrect-modifier, msg-value-loop, calls-loop, multiple-constructors, name-reused, naming-        
                        convention, variable-scope, protected-vars, public-mappings-nested, redundant-statements, reentrancy-benign, reentrancy-eth, reentrancy-events,
                        reentrancy-unlimited-gas, reentrancy-no-eth, return-bomb, return-leave, reused-constructor, rtlo, shadowing-abstract, incorrect-shift, similar-names,     
                        shadowing-state, storage-array, suicidal, tautological-compare, timestamp, too-many-digits, tx-origin, tautology, unchecked-lowlevel, unchecked-send,     
                        unchecked-transfer, unimplemented-functions, erc20-indexed, uninitialized-fptr-cst, uninitialized-local, uninitialized-state, uninitialized-storage,      
                        unprotected-upgrade, unused-return, unused-state, var-read-using-this, void-cst, write-after-write
  --list-detectors      List available detectors
  --exclude DETECTORS_TO_EXCLUDE
                        Comma-separated list of detectors that should be excluded
  --exclude-dependencies
                        Exclude results that are only related to dependencies
  --exclude-optimization
                        Exclude optimization analyses
  --exclude-informational
                        Exclude informational impact analyses
  --exclude-low         Exclude low impact analyses
  --exclude-medium      Exclude medium impact analyses
  --exclude-high        Exclude high impact analyses
  --fail-pedantic       Fail if any findings are detected
  --fail-low            Fail if any low or greater impact findings are detected
  --fail-medium         Fail if any medium or greater impact findings are detected
  --fail-high           Fail if any high impact findings are detected
  --fail-none, --no-fail-pedantic
                        Do not return the number of findings in the exit code
  --show-ignored-findings
                        Show all the findings

  
'''},

{'name':'oyente','docker':'oyente','command':'','image':'luongnguyen/oyente','example':'python /oyente/oyente/oyente.py -s /g4b/build/Example.bin -b -t xxx -ce','type':'build','usage':''' 
  usage: python /oyente/oyente/oyente.py [-h] (-s SOURCE | -ru REMOTE_URL) [--version] [-rmp REMAP]
                 [-t TIMEOUT] [-gl GAS_LIMIT] [-rp ROOT_PATH] [-ll LOOP_LIMIT]
                 [-dl DEPTH_LIMIT] [-ap ALLOW_PATHS] [-glt GLOBAL_TIMEOUT]
                 [-e] [-w] [-j] [-p] [-db] [-st] [-r] [-v] [-pl] [-b] [-a]
                 [-sj] [-gb] [-ce] [-gtc] [-sjo]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        local source file name. Solidity by default. Use -b to
                        process evm instead. Use stdin to read from stdin.
  -ru REMOTE_URL, --remoteURL REMOTE_URL
                        Get contract from remote URL. Solidity by default. Use
                        -b to process evm instead.
  --version             show program's version number and exit
  -rmp REMAP, --remap REMAP
                        Remap directory paths
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout for Z3 in ms.
  -gl GAS_LIMIT, --gaslimit GAS_LIMIT
                        Limit Gas
  -rp ROOT_PATH, --root-path ROOT_PATH
                        Root directory path used for the online version
  -ll LOOP_LIMIT, --looplimit LOOP_LIMIT
                        Limit number of loops
  -dl DEPTH_LIMIT, --depthlimit DEPTH_LIMIT
                        Limit DFS depth
  -ap ALLOW_PATHS, --allow-paths ALLOW_PATHS
                        Allow a given path for imports
  -glt GLOBAL_TIMEOUT, --global-timeout GLOBAL_TIMEOUT
                        Timeout for symbolic execution
  -e, --evm             Do not remove the .evm file.
  -w, --web             Run Oyente for web service
  -j, --json            Redirect results to a json file.
  -p, --paths           Print path condition information.
  -db, --debug          Display debug information
  -st, --state          Get input state from state.json
  -r, --report          Create .report file.
  -v, --verbose         Verbose output, print everything.
  -pl, --parallel       Run Oyente in parallel. Note: The performance may
                        depend on the contract
  -b, --bytecode        read bytecode in source instead of solidity file.
  -a, --assertion       Check assertion failures.
  -sj, --standard-json  Support Standard JSON input
  -gb, --globalblockchain
                        Integrate with the global ethereum blockchain
  -ce, --compilation-error
                        Display compilation errors
  -gtc, --generate-test-cases
                        Generate test cases each branch of symbolic execution
                        tree
  -sjo, --standard-json-output
                        Support Standard JSON output

'''},

    {'name': 'mythril','docker':'mythril', 'command': 'No','image':'smartbugs/mythril:0.23.15', 'example': 'analyze -f  /path/to/example/contract.bin --execution-timeout xxx', 'type':'build','usage':'''
     usage: [-h] [-v LOG_LEVEL]
            {safe-functions,analyze,a,disassemble,d,list-detectors,read-storage,function-to-hash,hash-to-address,version,help}
            ...

Security analysis of Ethereum smart contracts

positional arguments:
  {safe-functions,analyze,a,disassemble,d,list-detectors,read-storage,function-to-hash,hash-to-address,version,help}
                        Commands
    safe-functions      Check functions which are completely safe using
                        symbolic execution
    analyze (a)         Triggers the analysis of the smart contract
    disassemble (d)     Disassembles the smart contract
    list-detectors      Lists available detection modules
    read-storage        Retrieves storage slots from a given address through
                        rpc
    function-to-hash    Returns the hash signature of the function
    hash-to-address     converts the hashes in the blockchain to ethereum
                        address
    version             Outputs the version

optional arguments:
  -h, --help            show this help message and exit
  -v LOG_LEVEL          log level (0-5)'''},
    {'name': 'mythril','docker':'mythril', 'command': 'No','image':'smartbugs/mythril:0.23.15', 'example': 'analyze /path/to/example/contract.sol --execution-timeout xxx', 'type':'contracts','usage':'''
     usage: [-h] [-v LOG_LEVEL]
            {safe-functions,analyze,a,disassemble,d,list-detectors,read-storage,function-to-hash,hash-to-address,version,help}
            ...

Security analysis of Ethereum smart contracts

positional arguments:
  {safe-functions,analyze,a,disassemble,d,list-detectors,read-storage,function-to-hash,hash-to-address,version,help}
                        Commands
    safe-functions      Check functions which are completely safe using
                        symbolic execution
    analyze (a)         Triggers the analysis of the smart contract
    disassemble (d)     Disassembles the smart contract
    list-detectors      Lists available detection modules
    read-storage        Retrieves storage slots from a given address through
                        rpc
    function-to-hash    Returns the hash signature of the function
    hash-to-address     converts the hashes in the blockchain to ethereum
                        address
    version             Outputs the version

optional arguments:
  -h, --help            show this help message and exit
  -v LOG_LEVEL          log level (0-5)'''},
    {'name':'solhint','docker':'solhint','command':'solhint','image':'smartbugs/solhint:3.3.8','example':'solhint /path/to/example.sol','type':'contracts','usage':'''
    Usage: solhint [options] <file> [...other_files]

Don't use '' for the file path!
Options:

  -V, --version                           output the version number
  -f, --formatter [name]                  report formatter name (stylish, table, tap, unix, json, compact, sarif)
  -w, --max-warnings [maxWarningsNumber]  number of allowed warnings
  -c, --config [file_name]                file to use as your .solhint.json
  -q, --quiet                             report errors only - default: false
  --ignore-path [file_name]               file to use as your .solhintignore
  --fix                                   automatically fix problems and show report
  --noPrompt                              do not suggest to backup files when any `fix` option is selected
  --init                                  create configuration file for solhint
  --disc                                  do not check for solhint updates
  --save                                  save report to file on current folder
  -h, --help                              output usage information

Commands:

  stdin [options]                         linting of source code data provided to STDIN
  list-rules                              display covered rules of current .solhint.json     
'''},
    {'name':'semgrep','docker':'semgrep','command':'semgrep','image':'smartbugs/semgrep:c3a9f40','example':'semgrep --config p/smart-contracts example.sol','type':"contracts",'usage':'''
  Usage: pysemgrep [OPTIONS] COMMAND [ARGS]...

  To get started quickly, run `semgrep scan --config auto`

  Run `semgrep SUBCOMMAND --help` for more information on each subcommand

  If no subcommand is passed, will run `scan` subcommand by default

Options:
  -h, --help  Show this message and exit.

Commands:
  ci                   The recommended way to run semgrep in CI
  install-semgrep-pro  Install the Semgrep Pro Engine
  login                Obtain and save credentials for semgrep.dev
  logout               Remove locally stored credentials to semgrep.dev
  lsp                  [EXPERIMENTAL] Start the Semgrep LSP server
  publish              Upload rule to semgrep.dev
  scan                 Run semgrep rules on files
  shouldafound         Report a false negative in this project.
'''  }
]