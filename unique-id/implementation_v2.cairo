%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func getIdNumber{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(owner: felt) -> (
    id_number: felt
) {
    return (id_number=313337);
}
