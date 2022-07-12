#pragma once

float* fe_mfcc_16k_16b_mono(short *aBuffer, int aBufferSize,
                            int* n_frames, int* n_items_in_frame);

void fe_mfcc_init(void);

void fe_mfcc_free(void);
