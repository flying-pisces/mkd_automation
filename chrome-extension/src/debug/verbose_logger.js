/**
 * Verbose Logger for MKD Automation Chrome Extension
 * 
 * Provides a more detailed logging mechanism with verbosity levels.
 */

const VerboseLogger = (() => {
    let verbosityLevel = 0; // 0: off, 1: error, 2: warn, 3: info, 4: debug

    const setLevel = (level) => {
        verbosityLevel = level;
    };

    const log = (level, ...args) => {
        if (verbosityLevel >= level) {
            const prefix = `[${new Date().toISOString()}]`;
            switch (level) {
                case 1:
                    console.error(prefix, ...args);
                    break;
                case 2:
                    console.warn(prefix, ...args);
                    break;
                case 3:
                    console.info(prefix, ...args);
                    break;
                case 4:
                    console.debug(prefix, ...args);
                    break;
                default:
                    console.log(prefix, ...args);
            }
        }
    };

    return {
        setLevel,
        error: (...args) => log(1, ...args),
        warn: (...args) => log(2, ...args),
        info: (...args) => log(3, ...args),
        debug: (...args) => log(4, ...args),
    };
})();
