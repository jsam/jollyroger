// Generated by the gRPC C++ plugin.
// If you make any local change, they will be lost.
// source: transport.proto

#include "JRTransport/transport.pb.h"
#include "JRTransport/transport.grpc.pb.h"

#include <grpcpp/impl/codegen/async_stream.h>
#include <grpcpp/impl/codegen/async_unary_call.h>
#include <grpcpp/impl/codegen/channel_interface.h>
#include <grpcpp/impl/codegen/client_unary_call.h>
#include <grpcpp/impl/codegen/method_handler_impl.h>
#include <grpcpp/impl/codegen/rpc_service_method.h>
#include <grpcpp/impl/codegen/service_type.h>
#include <grpcpp/impl/codegen/sync_stream.h>

namespace jrtransport {

static const char* JRTransportService_method_names[] = {
  "/jrtransport.JRTransportService/Ping",
  "/jrtransport.JRTransportService/Auth",
};

std::unique_ptr< JRTransportService::Stub> JRTransportService::NewStub(const std::shared_ptr< ::grpc::ChannelInterface>& channel, const ::grpc::StubOptions& options) {
  (void)options;
  std::unique_ptr< JRTransportService::Stub> stub(new JRTransportService::Stub(channel));
  return stub;
}

JRTransportService::Stub::Stub(const std::shared_ptr< ::grpc::ChannelInterface>& channel)
  : channel_(channel), rpcmethod_Ping_(JRTransportService_method_names[0], ::grpc::internal::RpcMethod::NORMAL_RPC, channel)
  , rpcmethod_Auth_(JRTransportService_method_names[1], ::grpc::internal::RpcMethod::NORMAL_RPC, channel)
  {}

::grpc::Status JRTransportService::Stub::Ping(::grpc::ClientContext* context, const ::jrtransport::PingRequest& request, ::jrtransport::PongResponse* response) {
  return ::grpc::internal::BlockingUnaryCall(channel_.get(), rpcmethod_Ping_, context, request, response);
}

::grpc::ClientAsyncResponseReader< ::jrtransport::PongResponse>* JRTransportService::Stub::AsyncPingRaw(::grpc::ClientContext* context, const ::jrtransport::PingRequest& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderFactory< ::jrtransport::PongResponse>::Create(channel_.get(), cq, rpcmethod_Ping_, context, request, true);
}

::grpc::ClientAsyncResponseReader< ::jrtransport::PongResponse>* JRTransportService::Stub::PrepareAsyncPingRaw(::grpc::ClientContext* context, const ::jrtransport::PingRequest& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderFactory< ::jrtransport::PongResponse>::Create(channel_.get(), cq, rpcmethod_Ping_, context, request, false);
}

::grpc::Status JRTransportService::Stub::Auth(::grpc::ClientContext* context, const ::jrtransport::AuthRequest& request, ::jrtransport::AuthResponse* response) {
  return ::grpc::internal::BlockingUnaryCall(channel_.get(), rpcmethod_Auth_, context, request, response);
}

::grpc::ClientAsyncResponseReader< ::jrtransport::AuthResponse>* JRTransportService::Stub::AsyncAuthRaw(::grpc::ClientContext* context, const ::jrtransport::AuthRequest& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderFactory< ::jrtransport::AuthResponse>::Create(channel_.get(), cq, rpcmethod_Auth_, context, request, true);
}

::grpc::ClientAsyncResponseReader< ::jrtransport::AuthResponse>* JRTransportService::Stub::PrepareAsyncAuthRaw(::grpc::ClientContext* context, const ::jrtransport::AuthRequest& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderFactory< ::jrtransport::AuthResponse>::Create(channel_.get(), cq, rpcmethod_Auth_, context, request, false);
}

JRTransportService::Service::Service() {
  AddMethod(new ::grpc::internal::RpcServiceMethod(
      JRTransportService_method_names[0],
      ::grpc::internal::RpcMethod::NORMAL_RPC,
      new ::grpc::internal::RpcMethodHandler< JRTransportService::Service, ::jrtransport::PingRequest, ::jrtransport::PongResponse>(
          std::mem_fn(&JRTransportService::Service::Ping), this)));
  AddMethod(new ::grpc::internal::RpcServiceMethod(
      JRTransportService_method_names[1],
      ::grpc::internal::RpcMethod::NORMAL_RPC,
      new ::grpc::internal::RpcMethodHandler< JRTransportService::Service, ::jrtransport::AuthRequest, ::jrtransport::AuthResponse>(
          std::mem_fn(&JRTransportService::Service::Auth), this)));
}

JRTransportService::Service::~Service() {
}

::grpc::Status JRTransportService::Service::Ping(::grpc::ServerContext* context, const ::jrtransport::PingRequest* request, ::jrtransport::PongResponse* response) {
  (void) context;
  (void) request;
  (void) response;
  return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
}

::grpc::Status JRTransportService::Service::Auth(::grpc::ServerContext* context, const ::jrtransport::AuthRequest* request, ::jrtransport::AuthResponse* response) {
  (void) context;
  (void) request;
  (void) response;
  return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
}


}  // namespace jrtransport

