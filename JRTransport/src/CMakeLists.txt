# @brief
# @author  jsam <contact@justsam.io>

find_package(RocksDB)

set(protobuf_MODULE_COMPATIBLE TRUE)
include(FindProtobuf)
find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIR})

set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf)
set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)

# Find gRPC installation
find_package(gRPC REQUIRED)
set(_GRPC_GRPCPP_UNSECURE grpc++_unsecure)
set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:grpc_cpp_plugin>)


set(LIB_HEADERS
        ../include/JRUtils/MPMCQueue.h # Normal headers

        "${CMAKE_CURRENT_BINARY_DIR}/../include/JRTransport/Version.h" # Generated header
        ../include/JRTransport/transport.pb.h
        ../include/JRTransport/transport.grpc.pb.h


        ../include/JRTransport/CallDataBase.h # Normal headers
        ../include/JRTransport/PingCallData.h
        ../include/JRTransport/AuthCallData.h
        ../include/JRTransport/Server.h
        ../include/JRTransport/Client.h

        ../include/JRTransport/Node.h
        ../include/JRStore/Store.h
        )


set(LIB_SOURCES
        GeneratedSources/transport.pb.cc
        GeneratedSources/transport.grpc.pb.cc

        JRTransport/CallDataBase.cxx
        JRTransport/PingCallData.cxx
        JRTransport/AuthCallData.cxx
        JRTransport/Server.cxx
        JRTransport/Client.cxx
        JRTransport/Node.cxx

        JRStore/Store.cxx
        JRStore/HashID.cxx
        )

set(APP_HEADERS
        )

set(APP_SOURCES
        JRTransport/main.cxx
        )

# Define two variables in order not to repeat ourselves.
set(LIBRARY_NAME JRTransport)

# Define the library
add_library(${LIBRARY_NAME} SHARED ${LIB_SOURCES})

# Set the build version. It will be used in the name of the lib, with corresponding
# symlinks created. SOVERSION could also be specified for api version.
set_target_properties(${LIBRARY_NAME} PROPERTIES
        CXX_STANDARD_REQUIRED 17
        VERSION ${VERSION}  # ${VERSION} was defined in the main CMakeLists.
        FRAMEWORK FALSE
        PUBLIC_HEADER "${LIB_HEADERS}" # specify the public headers
        )

target_link_libraries(
        ${LIBRARY_NAME}
        ${GPR_LIBRARY}
        ${GRPC_LIBRARY}
        ${GRPCPP_LIBRARY}
        ${_GRPC_GRPCPP_UNSECURE}
        ${_PROTOBUF_LIBPROTOBUF}
        ${ROCKSDB_LIBRARIES}
)

# This is a make target, so you can do a "make JRTransportrunner"
set(APPLICATION_NAME JRTransportrunner)
add_executable(${APPLICATION_NAME} ${APP_SOURCES})

message(GRPC_STATUS "GRPClib: ${_GRPC_GRPCPP_UNSECURE}")
message(GRPC_STATUS "Protobuf: ${_PROTOBUF_LIBPROTOBUF}")

# Links the target exe (JRTransportrunner) against the library (libJRTransport) and other required libraries
target_link_libraries(${APPLICATION_NAME} ${LIBRARY_NAME}
        ${Boost_PROGRAM_OPTIONS_LIBRARY}

        )

# Says how and where to install software
# Targets:
#   * <prefix>/lib/<libraries>
#   * header location after install: <prefix>/include/<project>/*.h
#   * headers can be included by C++ code `#<project>/Bar.hpp>`
install(TARGETS ${LIBRARY_NAME} ${APPLICATION_NAME}
  EXPORT ${PROJECT_NAME}Targets            # for downstream dependencies
  ARCHIVE DESTINATION lib COMPONENT libs   # static lib
  RUNTIME DESTINATION bin COMPONENT libs   # binaries
  LIBRARY DESTINATION lib COMPONENT libs   # shared lib
  FRAMEWORK DESTINATION bin COMPONENT libs # for mac
  PUBLIC_HEADER DESTINATION include/${PROJECT_NAME} COMPONENT devel   # headers for mac (note the different component -> different package)
  INCLUDES DESTINATION include             # headers
)

