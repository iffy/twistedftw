// Copyright (c) The TwistedFTW Team
// See LICENSE for details.

var app = angular.module('article', []);

app.config(function($routeProvider, $locationProvider) {
    $routeProvider
        .when('/:category/:name', {
            templateUrl: function(params) {
                return 'articles/' + params.category + '/' + params.name + '.html';
            },
            controller: 'ArticleCtrl'
        })
        .otherwise({
            redirectTo: '/'
        });
    $locationProvider
        .html5Mode(false)
        .hashPrefix('!');
});

// XXX copied from mainapp.js
app.factory('ArticleIndex', function($http) {
    return $http.get('article_index.json')
        .then(function(d) {
            return d.data;
        });
});


app.controller('ArticleCtrl', function($scope, $route, $routeParams) {
    PR.prettyPrint();

})

app.controller('NavbarCtrl', function($scope, $location, ArticleIndex) {
    $scope.path = $location.path();
    $scope.current_section = '';
    $scope.current_article = '';
    $scope.index = ArticleIndex;

    $scope.$watch(function() {
        return $location.path();
    }, function(newvalue) {
        $scope.path = newvalue;
        var parts = newvalue.split('/');
        $scope.current_section = parts[1];
        $scope.current_article = parts[2];
    })
})