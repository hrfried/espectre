#ifndef LWIP_INET_H
#define LWIP_INET_H

#include <stdint.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#ifdef __cplusplus
extern "C" {
#endif

// IP address macros for formatting
#define IPSTR "%d.%d.%d.%d"
#define IP2STR(ipaddr) ((uint8_t *)&(ipaddr)->addr)[0], \
                       ((uint8_t *)&(ipaddr)->addr)[1], \
                       ((uint8_t *)&(ipaddr)->addr)[2], \
                       ((uint8_t *)&(ipaddr)->addr)[3]

// Network byte order conversion
// htons is typically provided by arpa/inet.h, but we ensure it's available
#ifndef htons
static inline uint16_t htons(uint16_t hostshort) {
  return ((hostshort & 0xFF) << 8) | ((hostshort & 0xFF00) >> 8);
}
#endif

#ifdef __cplusplus
}
#endif

#endif // LWIP_INET_H

