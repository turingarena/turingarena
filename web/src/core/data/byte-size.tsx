export function displayByteSize(bytes: number, maxRelevantBytes: number | null = null) {
  const kb = bytes / 1024;
  const mb = kb / 1024;

  const scale = maxRelevantBytes ?? bytes;

  if (scale > 100e6) {
    return `${mb.toFixed(1)} MB`;
  } else if (scale > 10e6) {
    return `${mb.toFixed(2)} MB`;
  } else if (scale > 1e6) {
    return `${kb.toFixed(0)} KB`;
  } else if (scale > 100e3) {
    return `${kb.toFixed(1)} KB`;
  } else if (scale > 10e3) {
    return `${kb.toFixed(2)} KB`;
  } else {
    return `${kb.toFixed(3)} KB`;
  }
}
