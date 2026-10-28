import * as sass from 'sass';
import * as fs from 'fs';
import * as path from 'path';
import {fileURLToPath} from 'url';
import parser from 'yargs-parser';

const baseDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const assetsDir = path.join(baseDir, 'assets/scss');
const scssInputDirs = ['admin', 'bootstrap5'];
const cssOutputDir = path.join(baseDir, 'cmsplugin_cascade/static/cascade/css');

console.log(`Compiling Sass files from ${assetsDir} to ${cssOutputDir}`);

export function compileSass(debug = false) {
	for (const inputDir of scssInputDirs) {
		for (const file of fs.readdirSync(path.join(assetsDir, inputDir)).filter(f => f.endsWith('.scss') && !f.startsWith('_'))) {
			const result = sass.compile(path.join(assetsDir, inputDir, file), {
				loadPaths: [baseDir],
				style: debug ? 'expanded' : 'compressed',
				sourceMap: debug,
				sourceMapIncludeSources: debug,
			});
			fs.mkdirSync(path.join(cssOutputDir, inputDir), {recursive: true});
			const outFile = path.join(cssOutputDir, inputDir, file.replace('.scss', '.css'));
			fs.writeFileSync(outFile, result.css);
			if (debug && result.sourceMap) {
				const mapFile = outFile + '.map';
				fs.writeFileSync(mapFile, JSON.stringify(result.sourceMap));
				fs.appendFileSync(outFile, `\n/*# sourceMappingURL=${path.basename(mapFile)} */\n`);
			}
			console.log(`sass: ${file} → ${outFile}`);
		}
	}
}

// Allow running standalone: node assets/sass.config.mjs [--debug]
if (process.argv[1] === fileURLToPath(import.meta.url)) {
	const buildOptions = parser(process.argv.slice(2), {boolean: ['debug']});
	compileSass(buildOptions.debug);
}
