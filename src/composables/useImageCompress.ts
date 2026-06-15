/**
 * Compress an image file before upload. Resizes to max dimension,
 * reduces quality to target size, returns as base64 data URL.
 */
export async function compressImage(file: File, maxPx = 1024, maxBytes = 512 * 1024): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        let { width, height } = img;
        // Scale down if needed
        if (width > maxPx || height > maxPx) {
          const ratio = Math.min(maxPx / width, maxPx / height);
          width = Math.round(width * ratio);
          height = Math.round(height * ratio);
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d')!;
        ctx.drawImage(img, 0, 0, width, height);

        // Try progressively lower quality to hit target size
        let quality = 0.8;
        const tryCompress = (q: number) => {
          const dataUrl = canvas.toDataURL('image/jpeg', q);
          const byteSize = Math.round(dataUrl.length * 0.75); // base64 → raw bytes approx
          if (byteSize > maxBytes && q > 0.4) {
            tryCompress(q - 0.15);
          } else {
            resolve(dataUrl);
          }
        };
        tryCompress(quality);
      };
      img.onerror = () => reject(new Error('Image load failed'));
      img.src = reader.result as string;
    };
    reader.onerror = () => reject(new Error('File read failed'));
    reader.readAsDataURL(file);
  });
}
