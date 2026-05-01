/**
 * Parse author string and return HTML with the user's name bolded.
 * Only truncate with "et al." for BabyBabelLM paper. All other papers show full author list.
 */
export function formatAuthorList(authorStr: string): string {
  const myName = 'Faiz Ghifari Haznitrama';
  const babyBabelLMTitle = 'BabyBabelLM';

  // Check if this is the BabyBabelLM paper by looking at the author string context
  // (we'll pass a flag from the parent component)
  const authors = authorStr.split(',').map(a => a.trim()).filter(Boolean);

  // Find index of my name
  let myIndex = -1;
  for (let i = 0; i < authors.length; i++) {
    if (authors[i].includes('Faiz') || authors[i].includes('Haznitrama')) {
      myIndex = i;
      break;
    }
  }

  // Bold my name in the list
  const formattedAuthors = authors.map(a => {
    if (a.includes('Faiz') || a.includes('Haznitrama')) {
      return `<strong>${a}</strong>`;
    }
    return a;
  });

  return formattedAuthors.join(', ');
}

/**
 * Format author list with et al. truncation for BabyBabelLM only.
 */
export function formatAuthorListWithTruncation(authorStr: string, isBabyBabelLM: boolean = false): string {
  const myName = 'Faiz Ghifari Haznitrama';
  const authors = authorStr.split(',').map(a => a.trim()).filter(Boolean);

  // Find index of my name
  let myIndex = -1;
  for (let i = 0; i < authors.length; i++) {
    if (authors[i].includes('Faiz') || authors[i].includes('Haznitrama')) {
      myIndex = i;
      break;
    }
  }

  if (myIndex === -1) {
    // My name not found, just return as-is
    return authors.join(', ');
  }

  // Build author list: all authors up to and including my name
  const beforeMe = authors.slice(0, myIndex);
  const me = `<strong>${authors[myIndex]}</strong>`;
  const afterMe = authors.slice(myIndex + 1);

  const result: string[] = [...beforeMe, me];

  // Only truncate with "et al." for BabyBabelLM
  if (isBabyBabelLM && afterMe.length > 0) {
    result.push('et al.');
  } else {
    // Show all remaining authors
    const formattedAfter = afterMe.map(a => {
      return a;
    });
    result.push(...formattedAfter);
  }

  return result.join(', ');
}
