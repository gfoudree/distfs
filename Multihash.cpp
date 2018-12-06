#include <cstring>
#include <cstdlib>
#include <exception>
#include <cassert>

#include "Multihash.h"

Multihash::Multihash(uint8_t functionCode, uint8_t digestLen, const char* digest) {
    assert(digestLen > 0);

    this->functionCode = functionCode;
    this->digestLen = digestLen;

    digest = new char[digestLen]();
    memcpy(this->digest, (const void*) digest, digestLen);
}

Multihash::~Multihash() {
    delete digest;
}
