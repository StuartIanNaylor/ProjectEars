#include "fe.h"
#include "c_speech_features.h"
#include "c_speech_features_fast.h"
#include <stddef.h>
#include <stdbool.h>

/*********************************************************************/

#define SAMPLE_RATE   16000
#define WIN_LEN       0.05f
#define WIN_STEP      0.02f
#define NUM_CEP       13
#define NUM_FILTERS   26
#define NUM_FFT       1024
#define LOWFREQ       0
#define HIGHFRWQ      SAMPLE_RATE/2
#define PREEMPH       0.97f
#define CEP_LIFTER    22
#define APPEND_ENERGY true

/*********************************************************************/

csf_float* fe_mfcc_16k_16b_mono(short *aBuffer, int aBufferSize, int* n_frames, int* n_items_in_frame)
{
  csf_float* mfcc = NULL;
  *n_items_in_frame = NUM_CEP;
  *n_frames = csf_mfcc(aBuffer, aBufferSize,
                       SAMPLE_RATE, WIN_LEN, WIN_STEP, NUM_CEP,
                       NUM_FILTERS, NUM_FFT, LOWFREQ, HIGHFRWQ, PREEMPH,
                       CEP_LIFTER, APPEND_ENERGY,
                       NULL, &mfcc);

  return mfcc;
}

/*********************************************************************/

void fe_mfcc_init(void)
{
  csf_magspec_init(NUM_FFT);
  csf_mfcc_init(NUM_CEP, NUM_FILTERS);
}

/*********************************************************************/

void fe_mfcc_free(void)
{
  csf_mfcc_free();
  csf_magspec_free();
}

/*********************************************************************/