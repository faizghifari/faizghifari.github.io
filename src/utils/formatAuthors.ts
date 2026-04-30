/**
 * Format author list: show authors until "Faiz Ghifari Haznitrama" is reached,
 * then continue with "et al." if there are more authors.
 * Bold the user's name.
 */
export function formatAuthors(authorsHtml: string): string {
  // authorsHtml is already HTML with <strong> tags for the user's name
  return authorsHtml;
}

/**
 * Parse author string and return HTML with the user's name bolded,
 * truncated with "et al." after the user's name if there are more authors.
 */
export function formatAuthorList(authorStr: string): string {
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
    // My name not found, just bold if "et al." style or return as-is
    return authors.map(a => a.includes(myName) ? `<strong>${a}</strong>` : a).join(', ');
  }

  // Build author list: all authors up to and including my name
  const beforeMe = authors.slice(0, myIndex);
  const me = `<strong>${authors[myIndex]}</strong>`;
  const afterMe = authors.slice(myIndex + 1);

  const result: string[] = [...beforeMe, me];

  // If there are authors after me, add "et al."
  if (afterMe.length > 0) {
    result.push('et al.');
  }

  return result.join(', ');
}
