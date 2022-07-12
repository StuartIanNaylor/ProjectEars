#include <stdlib.h>
#include "c_speech_features.h"
#include "c_speech_features_fast.h"
#include "tools/kiss_fftr.h"
#include <assert.h>

static kiss_fftr_cfg cfg;
static int gNFFT;

void
csf_magspec_init(int aNFFT)
{
  assert(cfg == NULL);
  gNFFT = aNFFT;
  cfg = kiss_fftr_alloc(aNFFT, 0, NULL, NULL);
  assert(cfg);
}

void
csf_magspec_free(void)
{
  assert(cfg);
  KISS_FFT_FREE(cfg);
}

csf_float*
csf_magspec(const csf_float* aFrames, int aNFrames, int aNFFT)
{
  int i, j, idx;
  const int fft_out = aNFFT / 2 + 1;

  assert(aNFFT == gNFFT);

  csf_float* mspec = (csf_float*)malloc(sizeof(csf_float) * aNFrames * fft_out);
  kiss_fft_cpx* out = (kiss_fft_cpx*)malloc(sizeof(kiss_fft_cpx) * fft_out);

  for (i = 0, idx = 0; i < aNFrames; i++) {
    // Compute the magnitude spectrum
    kiss_fftr(cfg, &(aFrames[i * aNFFT]), out);
    for (j = 0; j < fft_out; j++, idx++) {
      mspec[idx] = csf_sqrt(csf_pow(out[j].r, 2.0) + csf_pow(out[j].i, 2.0));
    }
  }

  free(out);
  return mspec;
}