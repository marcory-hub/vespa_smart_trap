
**One-line purpose:** edge impuls installation was not succesful
**Short summary:** The module XXX was compiled against a differnent Node.js version
**Agent:** archive

---


[Docs edge impulse cli installation](https://docs.edgeimpulse.com/tools/clis/edge-impulse-cli/installation)

1. Create an [Edge Impulse account](https://studio.edgeimpulse.com/signup).
2. Install [Python 3](https://www.python.org/) on your host computer.
3. Install [Node.js](https://nodejs.org/en/) v16.x+ or above on your host computer. 

definitive process for installing the `edge-impulse-cli` on macOS, addressing common issues related to `npm` and system `PATH` configuration.

**Step 1: Install and Configure nvm**
First, install Node Version Manager (`nvm`) to manage your Node.js installations and prevent permission issues.
- Remove any previous Homebrew Node.js installation
```sh
brew uninstall --ignore-dependencies node
```
- Install `nvm`:
```sh
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```
- Restart your terminal.

**Step 2: Clean `npm` Configuration and Install Node.js**
Next, you need to ensure `npm`'s configuration is clean and then use `nvm` to install Node.js.
- Install the latest LTS version of Node.js
```sh
nvm install --lts
```
- Clear any conflicting `npm` prefix settings: If prompted, run the command suggested by `nvm`.
```sh
nvm use --delete-prefix v22.18.0
```

**Step 3: Install and Manually Symlink `edge-impulse-cli`**

The `edge-impulse-cli` package often fails to create the main executable symlink during installation. This step addresses that issue directly.
- Install the package globally:
```sh
npm install -g edge-impulse-cli
```
- Manually create the symlink: The installer fails to create a symlink for the `edge-impulse-cli` command. You must manually create one pointing to the `daemon.js` file, which serves as the executable. Find the correct path to your daemon.js
```sh
ln -s /Users/YOUR_USER_NAME/.nvm/versions/node/v22.18.0/lib/node_modules/edge-impulse-cli/build/cli/daemon.js /Users/YOUR_USER_NAME/.nvm/versions/node/v22.18.0/bin/edge-impulse-cli
```

Mijn pad
```sh
ln -s /Users/md/.nvm/versions/node/v22.18.0/lib/node_modules/edge-impulse-cli/build/cli/daemon.js /Users/md/.nvm/versions/node/v22.18.0/bin/edge-impulse-cli
```

(Note: Replace `v22.18.0` with your installed Node.js version if different.)

**Step 4: Verify the Installation**
Confirm that the tool is now in your PATH and ready to use.
- Check for the executable:
```sh
which edge-impulse-cli
```
- Start the tool
```sh
edge-impulse-cli
```

---
Further troubleshooting
**The module XXX was compiled against a differnent Node.js version**

This error occurs when you have upgraded Node.js since installing the Edge Impulse CLI. Re-install the CLI via:

Copy

```
npm uninstall -g edge-impulse-cli
npm install -g edge-impulse-cli
```

This will rebuild the dependencies.