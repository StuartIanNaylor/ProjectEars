#include <stdio.h>
#include <assert.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "fe.h"

/*********************************************************************/

typedef struct 
{
  char     chunk_id[4];
  uint32_t chunk_size;
  char     format[4];
  char     fmtchunk_id[4];
  uint32_t fmtchunk_size;
  uint16_t audio_format;
  uint16_t num_channels;
  uint32_t sample_rate;
  uint32_t byte_rate;
  uint16_t block_align;
  uint16_t bits_per_sample;
  char     datachunk_id[4];
  uint32_t datachunk_size;
} wave_header_t;

/*********************************************************************/

typedef int16_t audio_sample_t;

/*********************************************************************/

#define RAW_CHUNK_SZ     (1600 * sizeof(audio_sample_t)) // 100ms
#define RAW_RING_SZ      (2 * RAW_CHUNK_SZ)
#define MFCC_FRAME_LEN   (13)

/*********************************************************************/

static bool read_block(void *ptr, size_t size, FILE *stream)
{
  return fread(ptr, size, 1, stream) == 1;
}

/*********************************************************************/

static audio_sample_t* read_wave_fd(FILE *fd, size_t *sz)
{
  wave_header_t header;

  assert(44 == sizeof header);
  assert(read_block(&header, sizeof header, fd));
  assert(memcmp(header.chunk_id, "RIFF" /* little-endian */, sizeof header.chunk_id) == 0);
  assert(header.chunk_size == 36 + header.datachunk_size);
  assert(memcmp(header.format, "WAVE", sizeof header.format) == 0);
  assert(memcmp(header.fmtchunk_id, "fmt ", sizeof header.fmtchunk_id) == 0);
  assert(header.fmtchunk_size == 16);
  assert(header.audio_format == 1);
  assert(header.num_channels == 1);
  assert(header.byte_rate == 32000);
  assert(header.block_align == 2);
  assert(header.sample_rate == 16000);
  assert(header.bits_per_sample == 16);
  assert(memcmp(header.datachunk_id, "data", sizeof header.datachunk_id) == 0);
  audio_sample_t *samples = malloc(header.datachunk_size);
  assert(samples);
  assert(read_block(samples, header.datachunk_size, fd));
  assert(fgetc(fd) == EOF);
  *sz = header.datachunk_size;

  return samples;
}

/*********************************************************************/

static audio_sample_t* read_wave(const char *path, size_t *sz)
{
  FILE *fd = fopen(path, "r");
  assert(fd);
  audio_sample_t *samples = read_wave_fd(fd, sz);
  fclose(fd);

  return samples;
}

/*********************************************************************/

static float* fe_16b_16k_mono(audio_sample_t *samples, size_t n_samples, int *n_frames)
{
  int n_items_in_frame = 0;
  float *feat;
  feat = fe_mfcc_16k_16b_mono(samples, n_samples, n_frames, &n_items_in_frame);
  assert(n_items_in_frame == MFCC_FRAME_LEN);
  assert(feat);

  return feat;
}

/*********************************************************************/

static void print_features(float *feat, size_t n_frames)
{
  for(int i = 0, idx = 0; i < n_frames; i++)
  {
    for(int k = 0; k < MFCC_FRAME_LEN; k++, idx++)
    {
      if(k)
      {
        printf(" ");
      }
      printf("%9.5f", feat[idx]);
    }
    printf("\n");
  }
}

/*********************************************************************/

static bool read_stdin(char *buf, size_t sz)
{
  return read_block(buf, sz, stdin);
}

/*********************************************************************/

int main(int argc, const char *argv[])
{
  fe_mfcc_init();

  int n_frames;
  if(argc > 1 && strcmp(argv[1], "-"))
  {
    size_t sz = 0;
    audio_sample_t *samples = read_wave(argv[1], &sz);
    assert(sz >= RAW_RING_SZ);
    float *feat = fe_16b_16k_mono(samples, sz / sizeof *samples, &n_frames);
    print_features(feat, n_frames);
    free(feat);
    free(samples);
  }
  else
  {
    char ring[RAW_RING_SZ];
    if(read_stdin(ring, RAW_CHUNK_SZ))
    {
      while(read_stdin(&ring[RAW_CHUNK_SZ], RAW_CHUNK_SZ))
      {
        float *feat = fe_16b_16k_mono((audio_sample_t*)ring, 2400, &n_frames);
        assert(n_frames == 6);
        print_features(&feat[MFCC_FRAME_LEN], n_frames - 1);
        free(feat);
        memcpy(ring, &ring[RAW_CHUNK_SZ], RAW_CHUNK_SZ);
      }
    }
  }

  fe_mfcc_free();

  return 0;
}

/*********************************************************************/