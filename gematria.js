const words = process.argv.slice(2);

function gematria(word) {
  return word
    .toUpperCase()
    .replace(/[^A-Z]/g, '')
    .split('')
    .reduce((sum, char) => sum + (char.charCodeAt(0) - 64), 0);
}

words.forEach(word => {
  console.log(`${word}: ${gematria(word)}`);
});
