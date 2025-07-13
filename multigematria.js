const words = process.argv.slice(2);

// BUILD MAPS
const simpleMap = {};
const jewishMap = {};
const qwertyMap = {};
const jewishQwertyMap = {};

// simple english A=1..Z=26
"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split('').forEach((c, i) => {
  simpleMap[c] = i + 1;
  jewishMap[c] = (i + 1) * 6;
});

// qwerty physical order
const qwertyLetters = 'QWERTYUIOPASDFGHJKLZXCVBNM'.split('');
qwertyLetters.forEach((c, i) => {
  qwertyMap[c] = i + 1;
  jewishQwertyMap[c] = (i + 1) * 6;
});

// HELPERS
function gematriaSum(word, map) {
  return word
    .toUpperCase()
    .replace(/[^A-Z]/g, '')
    .split('')
    .reduce((sum, char) => sum + (map[char] || 0), 0);
}

function isPrime(num) {
  if (num < 2) return false;
  for (let i = 2; i <= Math.sqrt(num); i++)
    if (num % i === 0) return false;
  return true;
}

function binaryString(str) {
  return str
    .split('')
    .map(c => c.charCodeAt(0).toString(2).padStart(8,'0'))
    .join(' ');
}

// CALCULATE
words.forEach(word => {
  const simple = gematriaSum(word, simpleMap);
  const jewish = gematriaSum(word, jewishMap);
  const qwerty = gematriaSum(word, qwertyMap);
  const jewishQwerty = gematriaSum(word, jewishQwertyMap);
  const bin = binaryString(word);

  console.log(`\n🌿 ${word}`);
  console.log(` Simple English:  ${simple} (${simple.toString(2)} bin) ${isPrime(simple) ? '🧬 prime' : ''}`);
  console.log(` Jewish:          ${jewish} (${jewish.toString(2)} bin) ${isPrime(jewish) ? '🧬 prime' : ''}`);
  console.log(` QWERTY:          ${qwerty} (${qwerty.toString(2)} bin) ${isPrime(qwerty) ? '🧬 prime' : ''}`);
  console.log(` Jewish-QWERTY:   ${jewishQwerty} (${jewishQwerty.toString(2)} bin) ${isPrime(jewishQwerty) ? '🧬 prime' : ''}`);
  console.log(` Binary of word:  ${bin}`);
});