// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ClassRegistry — each address registers its name once; the owner can deregister.
contract ClassRegistry {
    // ---------------------------------------------------------------- errors
    error EmptyName();
    error AlreadyRegistered(address who);
    error NotRegistered(address who);
    error NotOwner();

    // ---------------------------------------------------------------- events
    event Registered(address indexed who, string name);
    event Deregistered(address indexed who);

    // ---------------------------------------------------------------- state
    address public immutable owner;            // set once in the constructor
    mapping(address => string) public nameOf;  // address -> name
    address[] private members;                 // mappings can't iterate -> keep a list
    mapping(address => uint256) private indexPlusOne; // position in members (+1; 0 = absent)

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    // ---------------------------------------------------------------- write
    function register(string calldata name) external {
        if (bytes(name).length == 0) revert EmptyName();
        if (indexPlusOne[msg.sender] != 0) revert AlreadyRegistered(msg.sender);

        nameOf[msg.sender] = name;
        members.push(msg.sender);
        indexPlusOne[msg.sender] = members.length;

        emit Registered(msg.sender, name);
    }

    function deregister(address who) external onlyOwner {
        uint256 idx1 = indexPlusOne[who];
        if (idx1 == 0) revert NotRegistered(who);

        // swap-and-pop: move the last member into the removed slot, then pop
        uint256 idx = idx1 - 1;
        uint256 lastIdx = members.length - 1;
        if (idx != lastIdx) {
            address last = members[lastIdx];
            members[idx] = last;
            indexPlusOne[last] = idx1;
        }
        members.pop();

        delete indexPlusOne[who];
        delete nameOf[who];

        emit Deregistered(who);
    }

    // ---------------------------------------------------------------- read
    function isRegistered(address who) external view returns (bool) {
        return indexPlusOne[who] != 0;
    }

    function memberCount() external view returns (uint256) {
        return members.length;
    }

    function memberAt(uint256 i) external view returns (address) {
        return members[i];
    }

    function allMembers() external view returns (address[] memory) {
        return members;
    }
}
