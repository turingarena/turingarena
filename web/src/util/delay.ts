export async function delay(ms: number) {
  await new Promise(resolve => setTimeout(resolve, ms));
}

export async function animationFrame() {
  await new Promise(requestAnimationFrame);
}
