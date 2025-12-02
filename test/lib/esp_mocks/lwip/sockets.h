#ifndef LWIP_SOCKETS_H
#define LWIP_SOCKETS_H

// On native platform, use standard POSIX socket functions
// Just include the system headers - no need to redefine functions
#include <sys/socket.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#ifdef __cplusplus
extern "C" {
#endif

// Socket types are already defined in sys/socket.h
// Just ensure IPPROTO_UDP is available if not already defined
#ifndef IPPROTO_UDP
#define IPPROTO_UDP 17
#endif

#ifdef __cplusplus
}
#endif

#endif // LWIP_SOCKETS_H

