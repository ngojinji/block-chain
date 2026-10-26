const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ClassRegistry", function () {
  async function deployFixture() {
    const [owner, alice, bob, ...others] = await ethers.getSigners();
    const registry = await ethers.deployContract("ClassRegistry");
    return { registry, owner, alice, bob, others };
  }

  describe("deployment", function () {
    it("sets the deployer as owner and starts empty", async function () {
      const { registry, owner } = await loadFixture(deployFixture);
      expect(await registry.owner()).to.equal(owner.address);
      expect(await registry.memberCount()).to.equal(0n);
    });
  });

  describe("register", function () {
    it("stores the name and emits Registered", async function () {
      const { registry, alice } = await loadFixture(deployFixture);
      await expect(registry.connect(alice).register("Alice"))
        .to.emit(registry, "Registered")
        .withArgs(alice.address, "Alice");
      expect(await registry.nameOf(alice.address)).to.equal("Alice");
      expect(await registry.isRegistered(alice.address)).to.equal(true);
      expect(await registry.memberCount()).to.equal(1n);
      expect(await registry.memberAt(0)).to.equal(alice.address);
    });

    it("reverts on an empty name", async function () {
      const { registry, alice } = await loadFixture(deployFixture);
      await expect(registry.connect(alice).register(""))
        .to.be.revertedWithCustomError(registry, "EmptyName");
    });

    it("reverts on a second registration", async function () {
      const { registry, alice } = await loadFixture(deployFixture);
      await registry.connect(alice).register("Alice");
      await expect(registry.connect(alice).register("Alice again"))
        .to.be.revertedWithCustomError(registry, "AlreadyRegistered")
        .withArgs(alice.address);
    });
  });

  describe("deregister", function () {
    it("reverts for a non-owner with NotOwner", async function () {
      const { registry, alice, bob } = await loadFixture(deployFixture);
      await registry.connect(alice).register("Alice");
      await expect(registry.connect(bob).deregister(alice.address))
        .to.be.revertedWithCustomError(registry, "NotOwner");
    });

    it("reverts for an unknown address with NotRegistered", async function () {
      const { registry, bob } = await loadFixture(deployFixture);
      await expect(registry.deregister(bob.address))
        .to.be.revertedWithCustomError(registry, "NotRegistered")
        .withArgs(bob.address);
    });

    it("owner removes a member with swap-and-pop, keeping the array dense", async function () {
      const { registry, alice, bob, others } = await loadFixture(deployFixture);
      const carol = others[0];
      await registry.connect(alice).register("Alice");
      await registry.connect(bob).register("Bob");
      await registry.connect(carol).register("Carol");

      await expect(registry.deregister(alice.address))
        .to.emit(registry, "Deregistered")
        .withArgs(alice.address);

      expect(await registry.memberCount()).to.equal(2n);
      expect(await registry.memberAt(0)).to.equal(carol.address); // last moved into slot 0
      expect(await registry.memberAt(1)).to.equal(bob.address);
      expect(await registry.isRegistered(alice.address)).to.equal(false);
      expect(await registry.nameOf(alice.address)).to.equal("");

      // the removed address can register again
      await registry.connect(alice).register("Alice 2");
      expect(await registry.memberCount()).to.equal(3n);
    });
  });

  describe("many signers", function () {
    it("registers every signer with a different name and all round-trip", async function () {
      const { registry } = await loadFixture(deployFixture);
      const signers = (await ethers.getSigners()).slice(1, 16); // 15 accounts

      for (let i = 0; i < signers.length; i++) {
        await registry.connect(signers[i]).register(`Student ${i}`);
      }

      expect(await registry.memberCount()).to.equal(BigInt(signers.length));
      for (let i = 0; i < signers.length; i++) {
        expect(await registry.nameOf(signers[i].address)).to.equal(`Student ${i}`);
        expect(await registry.memberAt(i)).to.equal(signers[i].address);
      }
      expect(await registry.allMembers()).to.deep.equal(signers.map((s) => s.address));
    });
  });
});
