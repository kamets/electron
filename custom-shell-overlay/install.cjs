const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const rootDir = process.cwd();
const overlayDir = path.join(rootDir, 'custom-shell-overlay');

// 1. JSON Merging
function mergeJson(targetPath, overridePath) {
    if (!fs.existsSync(overridePath)) return;
    const target = JSON.parse(fs.readFileSync(targetPath, 'utf8'));
    const override = JSON.parse(fs.readFileSync(overridePath, 'utf8'));
    // Simple shallow merge for top-level keys, deep merge for existing objects
    for (const key in override) {
        if (typeof override[key] === 'object' && override[key] !== null && !Array.isArray(override[key]) && target[key]) {
             target[key] = { ...target[key], ...override[key] };
        } else {
            target[key] = override[key];
        }
    }
    fs.writeFileSync(targetPath, JSON.stringify(target, null, '\t'));
    console.log(`Merged ${path.basename(overridePath)} into ${path.basename(targetPath)}`);
}

mergeJson(path.join(rootDir, 'product.json'), path.join(overlayDir, 'branding', 'product.overrides.json'));
mergeJson(path.join(rootDir, 'package.json'), path.join(overlayDir, 'branding', 'package.overrides.json'));

// 2. Copy Modules
const contribDir = path.join(rootDir, 'src', 'vs', 'workbench', 'contrib');
const modulesDir = path.join(overlayDir, 'modules');

if (fs.existsSync(modulesDir)) {
    // Recursive copy modules to contrib
    // Using cp -r for simplicity in linux env
    try {
        execSync(`cp -r ${modulesDir}/* ${contribDir}/`);
        console.log('Copied modules to workbench/contrib');
    } catch (e) {
        console.error('Error copying modules:', e);
    }
}

// 3. Inject Imports
const mainFile = path.join(rootDir, 'src', 'vs', 'workbench', 'workbench.common.main.ts');
let mainContent = fs.readFileSync(mainFile, 'utf8');

const importLines = `
// Custom Shell Modules
import './contrib/financial/browser/financial.contribution.js';
import './contrib/ai/browser/ai.contribution.js';
`;

if (!mainContent.includes('Custom Shell Modules')) {
    const lastEndRegion = mainContent.lastIndexOf('//#endregion');
    if (lastEndRegion !== -1) {
        mainContent = mainContent.slice(0, lastEndRegion) + importLines + '\n' + mainContent.slice(lastEndRegion);
        fs.writeFileSync(mainFile, mainContent);
        console.log('Injected imports into workbench.common.main.ts');
    } else {
        console.warn('Could not find #endregion in main file, appending to end');
        fs.appendFileSync(mainFile, importLines);
    }
} else {
    console.log('Imports already injected');
}

console.log('Overlay installation complete!');
