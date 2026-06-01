import { LoremIpsum } from 'lorem-ipsum';

const lorem = new LoremIpsum({
  sentencesPerParagraph: {
    max: 8,
    min: 4,
  },
  wordsPerSentence: {
    max: 16,
    min: 8,
  },
});

function loremGenerator(quantity: number): string {
  let paragraphs = ``;

  for (let i = 0; i < quantity; i++) {
   paragraphs =  paragraphs.concat(`${lorem.generateParagraphs(1)} <br> <br>`);
  }

  return paragraphs;
}

export default loremGenerator;
