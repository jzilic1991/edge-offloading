FROM postgres:14
COPY app/*.sql /docker-entrypoint-initdb.d/
ENV POSTGRES_HOST_AUTH_METHOD=trust
EXPOSE 5432
USER postgres
