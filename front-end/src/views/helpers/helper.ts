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

function getInitials(name: string) {
    if (!name) return '??';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function ifCond(v1: any, operator: string, v2: any, options: any) {
    switch (operator) {
        case '==': return (v1 == v2) ? options.fn(this) : options.inverse(this);
        case '===': return (v1 === v2) ? options.fn(this) : options.inverse(this);
        case '!=': return (v1 != v2) ? options.fn(this) : options.inverse(this);
        case '!==': return (v1 !== v2) ? options.fn(this) : options.inverse(this);
        case '<': return (v1 < v2) ? options.fn(this) : options.inverse(this);
        case '<=': return (v1 <= v2) ? options.fn(this) : options.inverse(this);
        case '>': return (v1 > v2) ? options.fn(this) : options.inverse(this);
        case '>=': return (v1 >= v2) ? options.fn(this) : options.inverse(this);
        case '&&': return (v1 && v2) ? options.fn(this) : options.inverse(this);
        case '||': return (v1 || v2) ? options.fn(this) : options.inverse(this);
        default: return options.inverse(this);
    }
}

export default {listProfs, roundHelper, roundPercentageHelper, getInitials, ifCond};
