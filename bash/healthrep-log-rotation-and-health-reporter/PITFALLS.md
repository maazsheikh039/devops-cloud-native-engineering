# Strict-mode pitfalls verified in this project

- `((i++))` returns 1 when the old value is 0 -> use `i=$((i + 1))`
- `local x=$(cmd)` hides `cmd`'s exit status -> declare `local x`, then assign `x=$(cmd)`
- `cmd | head` under `pipefail` can return 141 (`SIGPIPE`) -> use `awk 'NR<=n'` or consume all input
- `set -e` is ignored inside functions/commands in `||`, `&&`, `if`, and `while` contexts
- Traps run between commands: always put timeouts on network calls
