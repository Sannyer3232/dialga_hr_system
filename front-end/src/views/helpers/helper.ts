interface Profs {
  name: string;
  room: number;
}
function listProfs(profs: Profs[]) {
  const list = profs.map((p) => `<li> ${p.name} - ${p.room} </li>`).join('');
  return `<ul> ${list} </ul>`;
}

function roundHelper(num: number, digits: number){

    return Number(num.toFixed(digits)); 
}

function roundPercentageHelper(num: number, digits: number){

    return (Number(num.toFixed(digits))*100); 
}

export default {listProfs, roundHelper, roundPercentageHelper};
