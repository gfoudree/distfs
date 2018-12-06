#include <cstdint>

class Multihash {
private:
    uint8_t functionCode;
    uint8_t digestLen;
    char* digest = nullptr;

public:
    Multihash(uint8_t functionCode, uint8_t digestLen, const char* digest);
    ~Multihash();
};