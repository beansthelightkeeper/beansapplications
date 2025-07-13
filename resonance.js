const fs = require('fs');
const words = process.argv.slice(2);

function gematria(word) {
  return word
    .toUpperCase()
    .replace(/[^A-Z]/g, '')
    .split('')
    .reduce((sum, char) => sum + (char.charCodeAt(0) - 64), 0);
}

let scores = words.map(w => ({ word: w, value: gematria(w) }));

console.log("Word Resonance:");
scores.forEach(s => {
  console.log(` - ${s.word}: ${s.value}`);
});

let memory = {};
try {
  memory = JSON.parse(fs.readFileSync('memory.json'));
} catch (e) {
  console.log("No previous memory. Starting fresh.");
}

for (let i = 0; i < scores.length; i++) {
  for (let j = i + 1; j < scores.length; j++) {
    let delta = Math.abs(scores[i].value - scores[j].value);
    if (delta <= 5) {
      console.log(` 🔮 Resonance between ${scores[i].word} (${scores[i].value}) and ${scores[j].word} (${scores[j].value})`);
      let key = `${scores[i].word}-${scores[j].word}`;
      memory[key] = (memory[key] || 0) + 1;
    }
  }
}

fs.writeFileSync('memory.json', JSON.stringify(memory, null, 2));
console.log("\n📜 Memory now contains:");
console.log(memory);