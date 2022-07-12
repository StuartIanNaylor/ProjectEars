#include "c_speech_features_fast.h"

#pragma weak csf_magspec_init
#pragma weak csf_magspec_free
#pragma weak csf_mfcc_init
#pragma weak csf_mfcc_free

void
csf_magspec_init(int aNFFT)
{
  (void)aNFFT;
}

void
csf_magspec_free(void){}

void
csf_mfcc_init(int aNCep, int aNFilters)
{
  (void)aNCep;
  (void)aNFilters;
}

void
csf_mfcc_free(void){}