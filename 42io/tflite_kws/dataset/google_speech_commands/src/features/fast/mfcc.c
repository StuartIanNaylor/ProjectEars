#include <stdlib.h>
#include "c_speech_features.h"
#include "c_speech_features_fast.h"
#include <assert.h>

static double sf1, sf2, *dct2f;
static int gNCep, gNFilters;

void
csf_mfcc_init(int aNCep, int aNFilters)
{
  int j, k, didx;

  assert(dct2f == NULL);
  dct2f = (double*)malloc(sizeof(double) * aNFilters * aNCep);
  assert(dct2f);

  gNCep = aNCep;
  gNFilters = aNFilters;

  for (j = 0, didx = 0; j < aNCep; j++)
    for (k = 0; k < aNFilters; k++, didx++)
        dct2f[didx] = cos(M_PI * j * (2 * k + 1) / (double)(2 * aNFilters));

  sf1 = csf_sqrt(1 / (4 * (double)aNFilters));
  sf2 = csf_sqrt(1 / (2 * (double)aNFilters));
}

void
csf_mfcc_free(void)
{
  assert(dct2f);
  free(dct2f);
}

int
csf_mfcc(const short* aSignal, unsigned int aSignalLen, int aSampleRate,
         csf_float aWinLen, csf_float aWinStep, int aNCep, int aNFilters,
         int aNFFT, int aLowFreq, int aHighFreq, csf_float aPreemph,
         int aCepLifter, int aAppendEnergy, csf_float* aWinFunc,
         csf_float** aMFCC)
{
  int i, j, k, idx, fidx, didx;
  csf_float* feat;
  csf_float* energy;

  assert(aNCep == gNCep);
  assert(aNFilters == gNFilters);

  int n_frames = csf_logfbank(aSignal, aSignalLen, aSampleRate, aWinLen, aWinStep,
                              aNFilters, aNFFT, aLowFreq, aHighFreq, aPreemph,
                              aWinFunc, &feat, aAppendEnergy ? &energy : NULL);

  // Perform DCT-II
  csf_float* mfcc = (csf_float*)malloc(sizeof(csf_float) * n_frames * aNCep);
  for (i = 0, idx = 0, fidx = 0; i < n_frames;
       i++, idx += aNCep, fidx += aNFilters) {
    for (j = 0, didx = 0; j < aNCep; j++) {
      double sum = 0.0;
      for (k = 0; k < aNFilters; k++, didx++) {
        sum += (double)feat[fidx+k] * dct2f[didx];
      }
      mfcc[idx+j] = (csf_float)(sum * 2.0 * ((i == 0 && j == 0) ? sf1 : sf2));
    }
  }

  // Free features array
  free(feat);

  // Apply a cepstral lifter
  if (aCepLifter != 0) {
    csf_lifter(mfcc, n_frames, aNCep, aCepLifter);
  }

  // Append energies
  if (aAppendEnergy) {
    for (i = 0, idx = 0; i < n_frames; i++, idx += aNCep) {
      mfcc[idx] = csf_log(energy[i]);
    }

    // Free energy array
    free(energy);
  }

  // Return MFCC features
  *aMFCC = mfcc;

  return n_frames;
}